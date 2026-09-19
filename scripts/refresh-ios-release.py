#!/usr/bin/env python3
"""Refresh the accepted iOS runtime with current launcher, identity editor and assets.

Requires an intact base checkout and its Xcode build log/object cache. No game data
or signing material is copied into the output. See the release source notes.
"""
import argparse,hashlib,importlib.util,json,pathlib,plistlib,shlex,shutil,subprocess
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--base-repo',type=pathlib.Path,required=True)
parser.add_argument('--base-build',type=pathlib.Path,required=True)
parser.add_argument('--build-log',type=pathlib.Path,required=True)
parser.add_argument('--base-runtime',type=pathlib.Path,required=True)
parser.add_argument('--translation',type=pathlib.Path,required=True)
parser.add_argument('--output',type=pathlib.Path,required=True)
args=parser.parse_args()
repo=pathlib.Path(__file__).resolve().parents[1]
out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
old=args.base_repo.resolve();cache=args.base_build.resolve()
oldapp=cache/'Release-iphoneos/KartPad.app'
app=out/'KartPad.app'
lines=args.build_log.read_text().splitlines()
spec=importlib.util.spec_from_file_location('build_provenance',repo/'scripts/write-build-provenance.py')
provenance=importlib.util.module_from_spec(spec);spec.loader.exec_module(provenance)
base_manifest=json.loads((oldapp/'kartpad-build.json').read_text())
for field,path in [('prepared_runtime',args.base_runtime),('translation',args.translation)]:
 if provenance.tree(path.resolve())!=base_manifest[field]: raise ValueError('Cached source no longer matches compilation manifest: '+field)
# The base checkout can acquire unrelated documentation/Android commits. Verify
# every original production file actually used by this iOS build against its
# recorded compilation revision, rather than claiming its current HEAD built it.
base_revision=base_manifest['source_revision']
paths=subprocess.check_output(['git','ls-tree','-r','--name-only',base_revision],cwd=old,text=True).splitlines()
for name in paths:
 if not (name.startswith(('apple/','runtime/','builder/','patches/')) or name in ['CMakeLists.txt','dependencies.lock.json'] or ('ios' in name and name.startswith('scripts/'))): continue
 expected=subprocess.check_output(['git','show',base_revision+':'+name],cwd=old)
 if (old/name).read_bytes()!=expected: raise ValueError('Cached production source changed: '+name)
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
host_sources=['KartPadRuntimeOverlayHost.mm','KartPadMiiManager.mm','KartPadPhysicalControllers.mm','SunPadControllerMapping.mm','SunPadDiagnostics.mm']
host_objects=[PathName.replace('.mm','.o') for PathName in host_sources]
commands=[]
def run(args):
 commands.append(args)
 (out/'commands.json').write_text(json.dumps(commands,indent=2))
 subprocess.run(args,cwd=out,check=True)
for source_name in host_sources:
 cmd=next(shlex.split(l) for l in lines if '/clang ' in l and ' -c ' in l and source_name in l and '/KartPadDual.build/' in l)
 expanded=[]
 for x in cmd:
  expanded.extend(shlex.split(pathlib.Path(x[1:]).read_text()) if x.startswith('@') else [x])
 cmd=[];i=0
 while i<len(expanded):
  x=expanded[i]
  if x in ['-include','-ivfsstatcache']:
   i+=2;continue
  for sub in ['/apple/','/runtime/include']:
   x=x.replace(str(old)+sub,str(repo)+sub)
  if x in ['-MF','--serialize-diagnostics','-o']:
   cmd.extend([x,str(out/pathlib.Path(expanded[i+1]).name)]);i+=2;continue
  cmd.append(x);i+=1
 cmd.extend(['-ffile-prefix-map='+str(repo)+'=KartPad','-fmacro-prefix-map='+str(repo)+'=KartPad'])
 run(cmd)
# Refresh only the settings overlay unity unit against the verified base runtime.
fps=out/'settings_overlay.cpp'
shutil.copyfile(repo/'vendor/runtimes/ios/runtime/src/settings_overlay.cpp',fps)
unity=cache/'CMakeFiles/mkw_runtime_common.dir/Unity/unity_runtime_4_cxx.cxx'
text=unity.read_text()
original=str(args.base_runtime.resolve()/'src/settings_overlay.cpp')
if original not in text: raise ValueError('Expected settings overlay include absent')
newunity=out/unity.name;newunity.write_text(text.replace(original,str(fps)))
cmd=next(shlex.split(l) for l in lines if '/clang ' in l and ' -c ' in l and 'unity_runtime_4_cxx.cxx' in l)
expanded=[]
for x in cmd: expanded.extend(shlex.split(pathlib.Path(x[1:]).read_text()) if x.startswith('@') else [x])
cmd=[];i=0
while i<len(expanded):
 x=expanded[i]
 if x=='-ivfsstatcache':i+=2;continue
 if x in ['-MF','--serialize-diagnostics','-o']:
  cmd.extend([x,str(out/pathlib.Path(expanded[i+1]).name)]);i+=2;continue
 cmd.append(str(newunity) if x==str(unity) else x);i+=1
run(cmd)
if app.exists(): shutil.rmtree(app)
shutil.copytree(oldapp,app)
for name in ['_CodeSignature','embedded.mobileprovision']:
 p=app/name
 if p.is_dir():shutil.rmtree(p)
 elif p.exists():p.unlink()
link=next(shlex.split(l) for l in lines if '/clang++ ' in l and l.endswith(str(oldapp/'KartPad')))
filelist=pathlib.Path(link[link.index('-filelist')+1]);objects=filelist.read_text().splitlines()
old_object=next(p for p in objects if p.endswith('/KartPadRuntimeOverlayHost.o'))
new_object=out/'KartPadRuntimeOverlayHost.o'
newlist=out/'KartPad.LinkFileList';newlist.write_text('\n'.join(str(out/pathlib.Path(p).name) if pathlib.Path(p).name in host_objects else p for p in objects)+'\n')
link[link.index('-filelist')+1]=str(newlist)
link[link.index('-o')+1]=str(app/'KartPad')
for i,p in enumerate(link):
 if p.endswith('/KartPad_dependency_info.dat'):link[i]=str(out/'KartPad_dependency_info.dat')
link=[str(out/'unity_runtime_4_cxx.o') if p.endswith('/unity_runtime_4_cxx.o') else p for p in link]
run(link)
run(['xcrun','actool',str(repo/'apple/ios/Assets.xcassets'),'--compile',str(app),'--output-format','human-readable-text','--notices','--warnings','--output-partial-info-plist',str(out/'asset-info.plist'),'--app-icon','AppIcon','--compress-pngs','--development-region','en','--target-device','iphone','--target-device','ipad','--minimum-deployment-target','16.0','--platform','iphoneos'])
info=plistlib.loads((app/'Info.plist').read_bytes());info.update(plistlib.loads((out/'asset-info.plist').read_bytes()));info['CFBundleShortVersionString']='0.4.24';info['CFBundleVersion']='49'
(app/'Info.plist').write_bytes(plistlib.dumps(info,fmt=plistlib.FMT_BINARY))
# Hash every refreshed project input, including headers and assets. Cached objects
# remain traceable to the verified base manifest, not claimed as a full rebuild.
inputs={str(p.relative_to(repo)):sha(p) for folder in ['apple/ios','apple/mobile','apple/shared','apple/third_party','runtime/include'] for p in (repo/folder).rglob('*') if p.is_file()}
record={'schema':2,'scope':'incremental mobile host, controls, diagnostics and FPS overlay refresh; remaining base runtime and translation cached','base_manifest':base_manifest,'refreshed_inputs':inputs,'refreshed_objects':{name:sha(out/name) for name in host_objects+['unity_runtime_4_cxx.o']},'fps_runtime_source_sha256':sha(fps),'ios_runtime_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo/'vendor/runtimes/ios',text=True).strip(),'binary_sha256':sha(app/'KartPad'),'cached_libraries':[{'name':pathlib.Path(p).name,'sha256':sha(p)} for p in link if p.endswith('.a')], 'cached_objects':[{'name':pathlib.Path(p).name,'sha256':sha(p)} for p in objects if pathlib.Path(p).name not in host_objects]}
(app/'kartpad-ui-composition.json').write_text(json.dumps(record,sort_keys=True,indent=2)+'\n')
(out/'composition.json').write_text(json.dumps(record,sort_keys=True,indent=2)+'\n')
print('READY:',app)

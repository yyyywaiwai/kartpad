#include <jni.h>
#include <SDL3/SDL_hints.h>

#include "kartpad/android/controller_mapping.hpp"
#include "kartpad/android/runtime_settings.hpp"

extern "C" JNIEXPORT void JNICALL
Java_dev_kartpad_android_KartPadActivity_nativeEnableActivityRecreation(
    JNIEnv*, jobject) {
  SDL_SetHint(SDL_HINT_ANDROID_ALLOW_RECREATE_ACTIVITY, "1");
}

extern "C" JNIEXPORT void JNICALL
Java_dev_kartpad_android_KartPadActivity_nativeApplyDisplaySettings(
    JNIEnv*, jobject, jboolean show_fps, jint fps_size, jint aspect_mode,
    jfloat resolution_scale) {
  kartpad::android::PublishDisplaySettings({
      .show_fps = show_fps == JNI_TRUE,
      .fps_size = static_cast<int>(fps_size),
      .aspect_mode = static_cast<int>(aspect_mode),
      .resolution_scale = static_cast<float>(resolution_scale),
  });
}

extern "C" JNIEXPORT void JNICALL
Java_dev_kartpad_android_KartPadActivity_nativeApplyControllerMapping(
    JNIEnv* env, jobject, jintArray values) {
  if (values == nullptr || env->GetArrayLength(values) != 7) return;
  jint raw[7]{};
  env->GetIntArrayRegion(values, 0, 7, raw);
  if (env->ExceptionCheck()) return;
  kartpad::android::ControllerButtonMapping mapping{};
  for (std::size_t index = 0; index < mapping.size(); ++index) {
    mapping[index] = static_cast<uint8_t>(raw[index]);
  }
  kartpad::android::PublishControllerButtonMapping(mapping);
}

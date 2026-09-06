import Foundation
import ScreenCaptureKit
import AVFoundation

// Compile with: swiftc -parse-as-library scripts/probe-macos-game-audio.swift -o /tmp/kartpad-audio-probe
// Usage: kartpad-audio-probe PID. Reads only the selected app's audio for 8 s.
// No audio samples or screen pixels are retained; stdout is content-free JSON.
// ScreenCaptureKit requires the host's existing Screen Recording permission.
final class Sink: NSObject, SCStreamOutput, SCStreamDelegate, @unchecked Sendable {
    let lock = NSLock()
    var buffers = 0, samples = 0, videoFrames = 0
    var squares = 0.0, peak = 0.0
    var errors: [String] = []
    func stream(_ stream: SCStream, didStopWithError error: Error) {
        lock.lock(); errors.append(error.localizedDescription); lock.unlock()
    }
    func stream(_ stream: SCStream, didOutputSampleBuffer sample: CMSampleBuffer, of type: SCStreamOutputType) {
        if type == .screen { lock.lock(); videoFrames += 1; lock.unlock(); return }
        guard type == .audio, let description = CMSampleBufferGetFormatDescription(sample) else { return }
        let format = AVAudioFormat(cmAudioFormatDescription: description)
        let frames = CMSampleBufferGetNumSamples(sample)
        guard frames > 0, let pcm = AVAudioPCMBuffer(pcmFormat: format, frameCapacity: AVAudioFrameCount(frames)) else { return }
        // Set byte sizes before copying, not afterward. A zero frameLength
        // otherwise produces -12731 and misleading all-silent measurements.
        pcm.frameLength = AVAudioFrameCount(frames)
        let status = CMSampleBufferCopyPCMDataIntoAudioBufferList(sample, at: 0, frameCount: Int32(frames), into: pcm.mutableAudioBufferList)
        guard status == noErr else {
            lock.lock(); errors.append("PCM copy failed: \(status)"); lock.unlock(); return
        }
        let asbd = format.streamDescription.pointee
        guard asbd.mBitsPerChannel == 32, asbd.mFormatFlags & kAudioFormatFlagIsFloat != 0 else { return }
        lock.lock(); defer { lock.unlock() }
        buffers += 1
        for buffer in UnsafeMutableAudioBufferListPointer(pcm.mutableAudioBufferList) {
            guard let raw = buffer.mData else { continue }
            let count = Int(buffer.mDataByteSize) / 4
            let values = raw.assumingMemoryBound(to: Float.self)
            for index in 0..<count {
                let value = Double(values[index])
                if value.isFinite { samples += 1; squares += value * value; peak = max(peak, abs(value)) }
            }
        }
    }
    func report() -> [String: Any] {
        lock.lock(); defer { lock.unlock() }
        return ["audioBuffers": buffers, "samples": samples, "videoFrames": videoFrames, "errors": errors,
                "peakDbfs": peak > 0 ? 20 * log10(peak) : -120,
                "rmsDbfs": squares > 0 ? 10 * log10(squares / Double(samples)) : -120]
    }
}

@main struct Probe {
    static func main() async throws {
        guard CommandLine.arguments.count == 2, let pid = Int32(CommandLine.arguments[1]), pid > 0 else {
            FileHandle.standardError.write(Data("usage: kartpad-audio-probe PID\n".utf8))
            exit(64)
        }
        let content = try await SCShareableContent.current
        guard let app = content.applications.first(where: { $0.processID == pid }), let display = content.displays.first else {
            throw NSError(domain: "KartPadAudioProbe", code: 1, userInfo: [NSLocalizedDescriptionKey: "Target app or display not found"])
        }
        let filter = SCContentFilter(display: display, including: [app], exceptingWindows: [])
        let config = SCStreamConfiguration()
        config.width = 2; config.height = 2
        config.minimumFrameInterval = CMTime(value: 1, timescale: 1)
        config.capturesAudio = true; config.excludesCurrentProcessAudio = false
        config.sampleRate = 48000; config.channelCount = 2
        let sink = Sink()
        let stream = SCStream(filter: filter, configuration: config, delegate: sink)
        let queue = DispatchQueue(label: "kartpad.audio.acceptance")
        try stream.addStreamOutput(sink, type: .screen, sampleHandlerQueue: queue)
        try stream.addStreamOutput(sink, type: .audio, sampleHandlerQueue: queue)
        try await stream.startCapture()
        try await Task.sleep(for: .seconds(8))
        try await stream.stopCapture()
        var report = sink.report(); report["pid"] = pid; report["bundleIdentifier"] = app.bundleIdentifier
        let passed = (report["samples"] as! Int) > 0 && (report["peakDbfs"] as! Double) > -70 && (report["errors"] as! [String]).isEmpty
        report["passed"] = passed
        report["durationSeconds"] = 8
        report["scope"] = "selected-app-host-audio"
        print(String(data: try JSONSerialization.data(withJSONObject: report, options: [.prettyPrinted, .sortedKeys]), encoding: .utf8)!)
        if !passed { exit(1) }
    }
}

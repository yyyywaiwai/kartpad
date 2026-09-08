package dev.kartpad.android

import android.content.ContentResolver
import android.net.Uri
import java.io.File

/** Narrow JNI boundary for the pinned Dolphin DiscIO source build. */
internal object KartPadDiscImageImporter {
    init {
        System.loadLibrary("kartpad_discio")
    }

    fun extract(resolver: ContentResolver, image: Uri, destination: File) {
        val descriptor = resolver.openFileDescriptor(image, "r")
            ?: throw IllegalArgumentException("The selected disc image could not be opened.")
        descriptor.use {
            nativeExtract(it.fd, destination.absolutePath)?.let {
                throw IllegalArgumentException(it)
            }
        }
    }

    private external fun nativeExtract(fd: Int, destination: String): String?
}

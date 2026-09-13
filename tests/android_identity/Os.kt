package android.system

import java.io.FileDescriptor
import java.io.IOException
import java.nio.channels.FileChannel
import java.nio.file.Path
import java.nio.file.StandardOpenOption
import java.util.IdentityHashMap

object OsConstants { const val O_RDONLY = 0 }

/** Checked sync seam; Android uses libc fsync, including the parent directory. */
object Os {
    var failSyncSuffix: String? = null
    var failSyncSkip = 0
    private val paths = IdentityHashMap<FileDescriptor, String>()
    private val directories = IdentityHashMap<FileDescriptor, FileChannel>()
    fun register(fd: FileDescriptor, path: String) { paths[fd] = path }
    fun open(path: String, flags: Int, mode: Int): FileDescriptor {
        check(flags == OsConstants.O_RDONLY && mode == 0)
        val fd = FileDescriptor()
        paths[fd] = path
        directories[fd] = FileChannel.open(Path.of(path), StandardOpenOption.READ)
        return fd
    }
    fun fsync(fd: FileDescriptor) {
        if (failSyncSuffix?.let { paths[fd]?.endsWith(it) } == true) {
            if (failSyncSkip > 0) failSyncSkip-- else throw IOException("injected sync failure")
        }
        directories[fd]?.force(true) ?: fd.sync()
    }
    fun close(fd: FileDescriptor) { directories.remove(fd)?.close(); paths.remove(fd) }
}

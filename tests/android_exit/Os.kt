package android.system
object Os {
    private val environment = mutableMapOf<String, String>()
    fun setenv(name: String, value: String, overwrite: Boolean) {
        if (overwrite || name !in environment) environment[name] = value
    }
    fun register(fd: java.io.FileDescriptor, path: String) = Unit
    fun unsetenv(name: String) { environment.remove(name) }
    fun getenv(name: String): String? = environment[name]
}

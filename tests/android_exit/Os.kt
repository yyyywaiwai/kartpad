package android.system
object Os {
    private val environment = mutableMapOf<String, String>()
    fun setenv(name: String, value: String, overwrite: Boolean) {
        if (overwrite || name !in environment) environment[name] = value
    }
    fun getenv(name: String): String? = environment[name]
}

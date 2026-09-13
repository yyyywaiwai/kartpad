// In-memory preferences for host behavior tests; this does not test Android disk I/O.
package android.content
class Context {
 companion object { const val MODE_PRIVATE = 0 }
 private val stores = mutableMapOf<String, Preferences>()
 fun getSharedPreferences(name: String, mode: Int): Preferences = stores.getOrPut(name) { Preferences() }
}
class Preferences {
 private val values = mutableMapOf<String, Int>()
 fun contains(key: String) = values.containsKey(key)
 fun getInt(key: String, default: Int) = values[key] ?: default
 fun edit() = Editor(values)
 class Editor(private val values: MutableMap<String, Int>) {
  fun putInt(key: String, value: Int): Editor { values[key] = value; return this }
  fun clear(): Editor { values.clear(); return this }
  fun apply() {}
 }
}

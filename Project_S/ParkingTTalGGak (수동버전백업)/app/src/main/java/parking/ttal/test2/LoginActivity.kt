package parking.ttal.test2

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch

class LoginActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        supportActionBar?.hide()
        setContentView(R.layout.activity_login)

        val loginRoot = findViewById<FrameLayout>(R.id.login_root_layout)
        ViewCompat.setOnApplyWindowInsetsListener(loginRoot) { v, insets ->
            val systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars())
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom)
            insets
        }

        val etUsername = findViewById<EditText>(R.id.etUsername)
        val etPassword = findViewById<EditText>(R.id.etPassword)
        val btnLogin = findViewById<Button>(R.id.btnLogin)
        val loadingProgress = findViewById<ProgressBar>(R.id.loadingProgress)

        btnLogin.setOnClickListener {
            val username = etUsername.text.toString().trim()
            val password = etPassword.text.toString().trim()

            if (username.isEmpty() || password.isEmpty()) {
                Toast.makeText(this, "The records are incomplete.", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            loadingProgress.visibility = View.VISIBLE
            btnLogin.isEnabled = false

            lifecycleScope.launch {
                try {
                    val response = RetrofitClient.instance.login(username, password)
                    val finalUrl = response.raw().request.url.toString()

                    if (response.isSuccessful && !finalUrl.contains("login")) {
                        Toast.makeText(this@LoginActivity, "PRESENCE DETECTED: $username", Toast.LENGTH_SHORT).show()
                        val intent = Intent(this@LoginActivity, MainActivity::class.java)
                        intent.putExtra("username", username)
                        startActivity(intent)
                        finish()
                    } else {
                        loadingProgress.visibility = View.GONE
                        btnLogin.isEnabled = true
                        Toast.makeText(this@LoginActivity, "The cipher does not match.", Toast.LENGTH_SHORT).show()
                    }
                } catch (e: Exception) {
                    loadingProgress.visibility = View.GONE
                    btnLogin.isEnabled = true
                    Toast.makeText(this@LoginActivity, "The connection falters", Toast.LENGTH_LONG).show()
                }
            }
        }
    }
}
package parking.ttal.test2

import android.content.Intent
import android.graphics.Color
import android.graphics.drawable.GradientDrawable
import android.os.Bundle
import android.view.Gravity
import android.view.View
import android.view.ViewGroup
import android.widget.*
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.*

class MainActivity : AppCompatActivity() {

    private lateinit var listView: ListView
    private lateinit var tvWelcome: TextView
    private var statusData: ParkingStatusResponse? = null
    private var currentUsername: String = ""

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val mainRoot = findViewById<LinearLayout>(R.id.main_root_layout)
        ViewCompat.setOnApplyWindowInsetsListener(mainRoot) { v, insets ->
            val systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars())
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom)
            insets
        }

        listView = findViewById(R.id.parkingList)
        tvWelcome = findViewById(R.id.tvWelcome)
        val btnLogout = findViewById<Button>(R.id.btnLogout)

        currentUsername = intent.getStringExtra("username") ?: "Unknown"
        tvWelcome.text = "ESTATE MAP"

        btnLogout.setOnClickListener {
            val intent = Intent(this, LoginActivity::class.java)
            startActivity(intent)
            finish()
        }

        lifecycleScope.launch {
            while (isActive) {
                fetchParkingStatus()
                delay(1000)
            }
        }
    }

    private suspend fun fetchParkingStatus() {
        try {
            val response = RetrofitClient.instance.getStatus()
            if (response.isSuccessful) {
                statusData = response.body()
                updateList()
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    private fun updateList() {
        val data = statusData ?: return
        val mcuIds = data.status.keys.toList().sortedBy { it.toIntOrNull() ?: 0 }

        val adapter = object : ArrayAdapter<String>(this, android.R.layout.simple_list_item_1, mcuIds) {
            override fun getView(position: Int, convertView: View?, parent: ViewGroup): View {
                val mcuId = getItem(position)!!

                val container = LinearLayout(context).apply {
                    orientation = LinearLayout.HORIZONTAL
                    setPadding(40, 50, 40, 50)
                    val params = LinearLayout.LayoutParams(
                        LinearLayout.LayoutParams.MATCH_PARENT,
                        LinearLayout.LayoutParams.WRAP_CONTENT
                    )
                    params.setMargins(0, 0, 0, 16)
                    layoutParams = params
                    background = context.getDrawable(R.drawable.card_dark)
                }

                val signal = data.status[mcuId] ?: 0
                val reserved = data.reservations[mcuId] ?: false
                val owner = data.reservation_owners[mcuId] ?: ""
                val isIllegal = data.illegal[mcuId] ?: false
                val remaining = data.timers[mcuId] ?: 0

                var statusColor = "#4E5452"
                var statusLabel = "AVAILABLE"
                var textColor = "#D1D1D1"

                if (signal == 3) {
                    statusColor = "#1A1A1A"
                    statusLabel = "CORRUPTED"
                } else if (isIllegal) {
                    statusColor = "#214159"
                    statusLabel = "TRESPASSED"
                } else if (reserved) {
                    statusColor = "#7A160E"
                    statusLabel = "CLAIMED BY $owner"
                    textColor = "#FFC107"
                } else if (signal == 1) {
                    statusColor = "#3E403F"
                    statusLabel = "OCCUPIED"
                }

                val idText = TextView(context).apply {
                    text = "SPOT [$mcuId]"
                    textSize = 16f
                    setTextColor(Color.parseColor(textColor))
                    typeface = android.graphics.Typeface.SERIF
                    layoutParams = LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f)
                }

                val statusText = TextView(context).apply {
                    val timer = if (reserved && remaining > 0) " (${remaining}s)" else ""
                    text = "$statusLabel$timer"
                    textSize = 13f
                    setTextColor(Color.parseColor(statusColor))
                    gravity = Gravity.END
                    layoutParams = LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1.5f)
                    isAllCaps = true
                }

                container.addView(idText)
                container.addView(statusText)

                container.setOnClickListener {
                    handleAction(mcuId, signal, reserved, owner, isIllegal, data.ban_user)
                }

                return container
            }
        }
        listView.adapter = adapter
    }

    private fun handleAction(id: String, signal: Int, reserved: Boolean, owner: String, isIllegal: Boolean, banned: Boolean) {
        val canReserve = !reserved && signal == 0 && !banned
        val canCompleteOrReport = reserved && signal == 1 && owner == currentUsername && !isIllegal

        val builder = AlertDialog.Builder(this)
        builder.setTitle("SPOT No.$id")

        if (canReserve) {
            builder.setMessage("Shall you claim this territory?")
            builder.setPositiveButton("CLAIM") { _, _ -> postAction("reserve", id) }
        } else if (canCompleteOrReport) {
            builder.setMessage("Choose your action.")
            builder.setPositiveButton("COMPLETE") { _, _ -> postAction("complete", id) }
            builder.setNeutralButton("REPORT") { _, _ -> postAction("report", id) }
        } else {
            val info = if(isIllegal) "A foul trespasser resides here." else if(reserved) "This land is already claimed." else "This path is blocked."
            builder.setMessage(info)
        }

        builder.setNegativeButton("RETURN", null)
        builder.show()
    }

    private fun postAction(type: String, id: String) {
        lifecycleScope.launch {
            try {
                val response = when(type) {
                    "reserve" -> RetrofitClient.instance.reserve(id)
                    "complete" -> RetrofitClient.instance.complete(id)
                    else -> RetrofitClient.instance.report(id)
                }
                if (response.isSuccessful) fetchParkingStatus()
            } catch (e: Exception) {
                Toast.makeText(this@MainActivity, "The connection falters...", Toast.LENGTH_SHORT).show()
            }
        }
    }
}
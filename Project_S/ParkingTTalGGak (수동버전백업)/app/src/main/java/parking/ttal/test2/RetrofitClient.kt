package parking.ttal.test2

import okhttp3.Cookie
import okhttp3.CookieJar
import okhttp3.HttpUrl
import okhttp3.OkHttpClient
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.*

// 데이터 모델
data class ParkingStatusResponse(
    val status: Map<String, Int>,
    val reservations: Map<String, Boolean>,
    val reservation_owners: Map<String, String?>,
    val timers: Map<String, Int>,
    val red_alerts: Map<String, Int>,
    val illegal: Map<String, Boolean>,
    val ban_user: Boolean
)

data class SimpleResponse(val success: Boolean)

// API 인터페이스
interface ApiService {
    @FormUrlEncoded
    @POST("/login")
    suspend fun login(
        @Field("username") user: String,
        @Field("password") pass: String
    ): Response<Void>

    @GET("/api/status")
    suspend fun getStatus(): Response<ParkingStatusResponse>

    @POST("/reserve/{mcu_id}")
    suspend fun reserve(@Path("mcu_id") mcuId: String): Response<SimpleResponse>

    @POST("/complete/{mcu_id}")
    suspend fun complete(@Path("mcu_id") mcuId: String): Response<SimpleResponse>

    @POST("/report/{mcu_id}")
    suspend fun report(@Path("mcu_id") mcuId: String): Response<SimpleResponse>
}

// 싱글톤 클라이언트 객체
object RetrofitClient {
    private val cookieJar = object : CookieJar {
        private val cookieStore = mutableMapOf<String, List<Cookie>>()

        override fun saveFromResponse(url: HttpUrl, cookies: List<Cookie>) {
            cookieStore[url.host] = cookies
        }

        override fun loadForRequest(url: HttpUrl): List<Cookie> {
            return cookieStore[url.host] ?: listOf()
        }
    }

    private val okHttpClient = OkHttpClient.Builder()
        .cookieJar(cookieJar) // Flask 세션 유지를 위해 필수
        .followRedirects(true) // 리다이렉트를 따라가야 최종 URL 확인 가능
        .build()

    val instance: ApiService by lazy {
        Retrofit.Builder()
            // 에뮬레이터: 10.0.2.2 / 실제폰: 서버 컴퓨터 IP
            .baseUrl("http://10.53.184.208:1557")
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(ApiService::class.java)
    }
}
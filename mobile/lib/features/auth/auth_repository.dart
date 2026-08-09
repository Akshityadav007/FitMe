import '../../core/network/api_client.dart';
import 'auth_models.dart';

class AuthRepository {
  const AuthRepository(this._apiClient, this._sessionStorage);

  final ApiClient _apiClient;
  final dynamic _sessionStorage;

  Future<AuthResponse> register({
    required String email,
    required String password,
    String? firstName,
    String? lastName,
    String? goal,
    String? activityLevel,
    String? dietaryPreferences,
  }) async {
    final json = await _apiClient.postJson('/auth/register', {
      'email': email,
      'password': password,
      'first_name': firstName,
      'last_name': lastName,
      'goal': goal,
      'activity_level': activityLevel,
      'dietary_preferences': dietaryPreferences,
    });
    final authResponse = AuthResponse.fromJson(json);
    await _sessionStorage.saveToken(authResponse.accessToken);
    return authResponse;
  }

  Future<AuthResponse> login({
    required String email,
    required String password,
  }) async {
    final json = await _apiClient.postJson('/auth/login', {
      'email': email,
      'password': password,
    });
    final authResponse = AuthResponse.fromJson(json);
    await _sessionStorage.saveToken(authResponse.accessToken);
    return authResponse;
  }

  Future<UserProfile> fetchProfile(String token) async {
    final json = await _apiClient.getJson('/profile/me', authToken: token);
    return UserProfile.fromJson(json);
  }

  Future<UserProfile> updateProfile(String token, Map<String, dynamic> payload) async {
    final json = await _apiClient.putJson('/profile/me', payload, authToken: token);
    return UserProfile.fromJson(json);
  }

  Future<NutritionTarget> fetchNutritionTargets(String token) async {
    final json = await _apiClient.getJson('/nutrition-targets/me', authToken: token);
    return NutritionTarget.fromJson(json);
  }

  Future<NutritionTarget> updateNutritionTargets(
    String token,
    Map<String, dynamic> payload,
  ) async {
    final json = await _apiClient.putJson(
      '/nutrition-targets/me',
      payload,
      authToken: token,
    );
    return NutritionTarget.fromJson(json);
  }

  Future<void> signOut() async {
    await _sessionStorage.clearToken();
  }

  Future<String?> readToken() async {
    return _sessionStorage.readToken();
  }
}

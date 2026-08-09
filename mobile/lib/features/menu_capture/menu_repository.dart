import '../../core/network/api_client.dart';
import 'menu_models.dart';

class MenuCaptureRepository {
  const MenuCaptureRepository(this._apiClient);

  final ApiClient _apiClient;

  Future<MenuImage> upload({
    required String token,
    required List<int> bytes,
    required String contentType,
  }) async {
    final json = await _apiClient.postBytes(
      '/menu-images/upload',
      body: bytes,
      contentType: contentType,
      authToken: token,
    );
    return MenuImage.fromJson(json);
  }

  Future<MenuImageProcess> process({
    required String token,
    required String menuImageId,
  }) async {
    final json = await _apiClient.postJson(
      '/menu-images/$menuImageId/process',
      const {},
      authToken: token,
    );
    return MenuImageProcess.fromJson(json);
  }

  Future<Map<String, Object?>> confirmItem({
    required String token,
    required String menuItemId,
    required String date,
    required String mealType,
    required double quantityG,
    String? notes,
  }) async {
    return _apiClient.postJson(
      '/menu-items/$menuItemId/confirm',
      {
        'date': date,
        'meal_type': mealType,
        'quantity_g': quantityG,
        if (notes != null) 'notes': notes,
      },
      authToken: token,
    );
  }
}

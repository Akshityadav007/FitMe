import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../auth/auth_providers.dart';
import 'menu_models.dart';
import 'menu_repository.dart';

final menuCaptureRepositoryProvider = Provider<MenuCaptureRepository>((ref) {
  return MenuCaptureRepository(ref.watch(apiClientProvider));
});

enum MenuCaptureStatus { idle, uploading, processing, done, error }

class MenuCaptureState {
  const MenuCaptureState({
    this.status = MenuCaptureStatus.idle,
    this.items = const [],
    this.error,
  });

  final MenuCaptureStatus status;
  final List<MenuImageItem> items;
  final String? error;

  bool get busy => status == MenuCaptureStatus.uploading || status == MenuCaptureStatus.processing;

  MenuCaptureState copyWith({
    MenuCaptureStatus? status,
    List<MenuImageItem>? items,
    String? error,
  }) {
    return MenuCaptureState(
      status: status ?? this.status,
      items: items ?? this.items,
      error: error,
    );
  }
}

class MenuCaptureController extends StateNotifier<MenuCaptureState> {
  MenuCaptureController(this._repository, this._readToken)
      : super(const MenuCaptureState());

  final MenuCaptureRepository _repository;
  final String? Function() _readToken;

  Future<void> uploadAndProcess({
    required List<int> bytes,
    required String contentType,
  }) async {
    final token = _readToken();
    if (token == null) {
      state = state.copyWith(status: MenuCaptureStatus.error, error: 'Not authenticated.');
      return;
    }
    state = state.copyWith(status: MenuCaptureStatus.uploading, error: null);
    try {
      final uploaded = await _repository.upload(
        token: token,
        bytes: bytes,
        contentType: contentType,
      );
      state = state.copyWith(status: MenuCaptureStatus.processing);
      final processed = await _repository.process(token: token, menuImageId: uploaded.id);
      state = state.copyWith(status: MenuCaptureStatus.done, items: processed.items);
    } catch (error) {
      state = state.copyWith(status: MenuCaptureStatus.error, error: error.toString());
    }
  }

  void reset() {
    state = const MenuCaptureState();
  }
}

final menuCaptureControllerProvider =
    StateNotifierProvider.autoDispose<MenuCaptureController, MenuCaptureState>((ref) {
  return MenuCaptureController(
    ref.watch(menuCaptureRepositoryProvider),
    () => ref.read(authTokenProvider).value,
  );
});

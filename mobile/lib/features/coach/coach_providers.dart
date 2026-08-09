import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../auth/auth_providers.dart';
import 'coach_models.dart';
import 'coach_repository.dart';

final coachRepositoryProvider = Provider<CoachRepository>((ref) {
  return CoachRepository(ref.watch(apiClientProvider));
});

final coachConversationProvider =
    StateNotifierProvider<CoachConversationController, CoachConversationState>((ref) {
  return CoachConversationController(ref);
});

class CoachConversationState {
  const CoachConversationState({
    this.conversationId,
    this.messages = const [],
    this.loading = false,
    this.error,
  });

  final String? conversationId;
  final List<CoachMessage> messages;
  final bool loading;
  final String? error;

  CoachConversationState copyWith({
    String? conversationId,
    List<CoachMessage>? messages,
    bool? loading,
    String? error,
    bool clearError = false,
  }) {
    return CoachConversationState(
      conversationId: conversationId ?? this.conversationId,
      messages: messages ?? this.messages,
      loading: loading ?? this.loading,
      error: clearError ? null : (error ?? this.error),
    );
  }
}

class CoachConversationController extends StateNotifier<CoachConversationState> {
  CoachConversationController(this._ref)
      : super(const CoachConversationState(loading: true)) {
    _loadHistory();
  }

  final Ref _ref;

  Future<void> _loadHistory() async {
    state = state.copyWith(loading: false);
  }

  Future<void> send(String message) async {
    final token = _ref.read(authTokenProvider).value;
    if (token == null) {
      state = state.copyWith(error: 'Not authenticated.');
      return;
    }
    final trimmed = message.trim();
    if (trimmed.isEmpty || state.loading) {
      return;
    }

    final userMessage = CoachMessage(role: 'user', content: trimmed);
    state = state.copyWith(
      messages: [...state.messages, userMessage],
      loading: true,
      error: null,
    );

    try {
      final response = await _ref.read(coachRepositoryProvider).sendMessage(
            token: token,
            message: trimmed,
            conversationId: state.conversationId,
          );
      final assistantMessage = CoachMessage(role: 'assistant', content: response.reply);
      state = state.copyWith(
        conversationId: response.conversationId,
        messages: [...state.messages, assistantMessage],
        loading: false,
      );
    } catch (error) {
      state = state.copyWith(loading: false, error: error.toString());
    }
  }
}

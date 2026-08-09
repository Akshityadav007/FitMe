import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../auth/auth_providers.dart';
import 'recommendation_models.dart';
import 'recommendation_repository.dart';

final recommendationRepositoryProvider = Provider<RecommendationRepository>((ref) {
  return RecommendationRepository(ref.watch(apiClientProvider));
});

final recommendationProvider = FutureProvider.autoDispose<Recommendation>((ref) {
  final token = ref.watch(authTokenProvider).value;
  if (token == null) {
    throw StateError('Not authenticated.');
  }
  final date = DateTime.now().toIso8601String().substring(0, 10);
  return ref.watch(recommendationRepositoryProvider).recommend(token: token, date: date);
});

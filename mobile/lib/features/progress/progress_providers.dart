import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../auth/auth_providers.dart';
import 'progress_models.dart';
import 'progress_repository.dart';

final progressRepositoryProvider = Provider<ProgressRepository>((ref) {
  return ProgressRepository(ref.watch(apiClientProvider));
});

final weeklyProgressProvider = FutureProvider.autoDispose<WeeklyProgress>((ref) {
  final token = ref.watch(authTokenProvider).value;
  if (token == null) {
    throw StateError('Not authenticated.');
  }
  final endDate = DateTime.now().toIso8601String().substring(0, 10);
  return ref.watch(progressRepositoryProvider).fetchWeekly(token: token, endDate: endDate);
});

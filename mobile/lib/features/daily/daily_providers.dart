import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../auth/auth_providers.dart';
import 'daily_models.dart';
import 'daily_repository.dart';

final dailyRepositoryProvider = Provider<DailyRepository>((ref) {
  return DailyRepository(ref.watch(apiClientProvider));
});

final dailySummaryProvider = FutureProvider.autoDispose<DailySummary>((ref) {
  final token = ref.watch(authTokenProvider).value;
  if (token == null) {
    throw StateError('Not authenticated.');
  }
  final date = DateTime.now().toIso8601String().substring(0, 10);
  return ref.watch(dailyRepositoryProvider).fetchSummary(token: token, date: date);
});

final nutritionTargetsProvider = FutureProvider.autoDispose<NutritionTarget>((ref) {
  final token = ref.watch(authTokenProvider).value;
  if (token == null) {
    throw StateError('Not authenticated.');
  }
  return ref.watch(dailyRepositoryProvider).fetchTargets(token: token);
});

final logWaterProvider = FutureProvider.autoDispose.family<void, int>((ref, amountMl) async {
  final token = ref.watch(authTokenProvider).value;
  if (token == null) {
    throw StateError('Not authenticated.');
  }
  final date = DateTime.now().toIso8601String().substring(0, 10);
  await ref.watch(dailyRepositoryProvider).logWater(
        token: token,
        date: date,
        amountMl: amountMl,
      );
});

final logStepsProvider = FutureProvider.autoDispose.family<void, int>((ref, steps) async {
  final token = ref.watch(authTokenProvider).value;
  if (token == null) {
    throw StateError('Not authenticated.');
  }
  final date = DateTime.now().toIso8601String().substring(0, 10);
  await ref.watch(dailyRepositoryProvider).logSteps(token: token, date: date, steps: steps);
});

final logSleepProvider = FutureProvider.autoDispose.family<void, int>((ref, durationMinutes) async {
  final token = ref.watch(authTokenProvider).value;
  if (token == null) {
    throw StateError('Not authenticated.');
  }
  final date = DateTime.now().toIso8601String().substring(0, 10);
  await ref.watch(dailyRepositoryProvider).logSleep(
        token: token,
        date: date,
        durationMinutes: durationMinutes,
      );
});

final logWorkoutProvider =
    FutureProvider.autoDispose.family<void, ({String name, int? durationMinutes})>(
  (ref, workout) async {
    final token = ref.watch(authTokenProvider).value;
    if (token == null) {
      throw StateError('Not authenticated.');
    }
    final date = DateTime.now().toIso8601String().substring(0, 10);
    await ref.watch(dailyRepositoryProvider).logWorkout(
          token: token,
          date: date,
          name: workout.name,
          durationMinutes: workout.durationMinutes,
        );
  },
);

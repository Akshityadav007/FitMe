import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../auth/auth_providers.dart';
import 'health_models.dart';
import 'health_repository.dart';

final healthRepositoryProvider = Provider<HealthRepository>((ref) {
  return HealthRepository(ref.watch(apiClientProvider));
});

final healthStatusProvider = FutureProvider<HealthResponse>((ref) {
  return ref.watch(healthRepositoryProvider).fetchHealth();
});

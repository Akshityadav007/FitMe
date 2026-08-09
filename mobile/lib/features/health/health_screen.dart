import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'health_providers.dart';

class HealthScreen extends ConsumerWidget {
  const HealthScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final healthStatus = ref.watch(healthStatusProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('FitMe')),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: healthStatus.when(
            loading: () => const CircularProgressIndicator(),
            error: (error, stackTrace) => _StatusPanel(
              title: 'Backend unavailable',
              message: error.toString(),
              action: FilledButton.icon(
                onPressed: () => ref.invalidate(healthStatusProvider),
                icon: const Icon(Icons.refresh),
                label: const Text('Retry'),
              ),
            ),
            data: (health) => _StatusPanel(
              title: 'Backend connected',
              message:
                  '${health.service} responded at ${health.checkedAt.toLocal()}',
              action: OutlinedButton.icon(
                onPressed: () => ref.invalidate(healthStatusProvider),
                icon: const Icon(Icons.refresh),
                label: const Text('Check again'),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _StatusPanel extends StatelessWidget {
  const _StatusPanel({
    required this.title,
    required this.message,
    required this.action,
  });

  final String title;
  final String message;
  final Widget action;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return ConstrainedBox(
      constraints: const BoxConstraints(maxWidth: 440),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(title, style: textTheme.headlineSmall),
          const SizedBox(height: 12),
          Text(message, style: textTheme.bodyMedium),
          const SizedBox(height: 20),
          Align(alignment: Alignment.centerLeft, child: action),
        ],
      ),
    );
  }
}

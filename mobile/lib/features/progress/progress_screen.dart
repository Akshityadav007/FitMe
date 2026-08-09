import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'progress_models.dart';
import 'progress_providers.dart';

class ProgressScreen extends ConsumerWidget {
  const ProgressScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final progress = ref.watch(weeklyProgressProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Weekly progress')),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(weeklyProgressProvider);
          await ref.read(weeklyProgressProvider.future);
        },
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            progress.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (error, _) => _ErrorCard(
                message: error.toString(),
                onRetry: () => ref.invalidate(weeklyProgressProvider),
              ),
              data: (data) => _ProgressBody(data: data),
            ),
          ],
        ),
      ),
    );
  }
}

class _ProgressBody extends StatelessWidget {
  const _ProgressBody({required this.data});

  final WeeklyProgress data;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        _SummaryCard(
          title: 'Nutrition',
          rows: [
            _Row('Days logged', '${data.nutrition.daysLogged}'),
            _Row('Avg calories', data.nutrition.averageCalories?.toString() ?? '—'),
            _Row('Avg protein', data.nutrition.averageProteinG != null
                ? '${data.nutrition.averageProteinG} g'
                : '—'),
            _Row('Protein adherence',
                data.nutrition.proteinAdherencePercent != null
                    ? '${data.nutrition.proteinAdherencePercent}%'
                    : '—'),
          ],
        ),
        const SizedBox(height: 12),
        _SummaryCard(
          title: 'Hydration',
          rows: [
            _Row('Days logged', '${data.hydration.daysLogged}'),
            _Row('Avg water', data.hydration.averageWaterMl != null
                ? '${data.hydration.averageWaterMl} ml'
                : '—'),
            _Row('Water adherence',
                data.hydration.waterAdherencePercent != null
                    ? '${data.hydration.waterAdherencePercent}%'
                    : '—'),
          ],
        ),
        const SizedBox(height: 12),
        _SummaryCard(
          title: 'Weight',
          rows: [
            _Row('7-day average', data.weight.sevenDayAverageKg?.toString() ?? '—'),
            _Row('Trend', data.weight.trendKg != null
                ? '${data.weight.trendKg!.toStringAsFixed(2)} kg'
                : '—'),
            _Row('Rate / week', data.weight.rateOfChangeKgPerWeek != null
                ? '${data.weight.rateOfChangeKgPerWeek!.toStringAsFixed(2)} kg'
                : '—'),
          ],
        ),
        const SizedBox(height: 12),
        _SummaryCard(
          title: 'Activity',
          rows: [
            _Row('Avg steps', data.steps.averageSteps?.toString() ?? '—'),
            _Row('Avg sleep', data.sleep.averageSleepMinutes != null
                ? '${data.sleep.averageSleepMinutes} min'
                : '—'),
            _Row('Workout days', '${data.training.workoutDays}'),
            _Row('Training adherence',
                data.training.trainingAdherencePercent != null
                    ? '${data.training.trainingAdherencePercent}%'
                    : '—'),
          ],
        ),
      ],
    );
  }
}

class _SummaryCard extends StatelessWidget {
  const _SummaryCard({required this.title, required this.rows});

  final String title;
  final List<_Row> rows;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),
            for (final row in rows) Padding(
              padding: const EdgeInsets.only(bottom: 4),
              child: row,
            ),
          ],
        ),
      ),
    );
  }
}

class _Row extends StatelessWidget {
  const _Row(this.label, this.value);

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [Text(label), Text(value)],
    );
  }
}

class _ErrorCard extends StatelessWidget {
  const _ErrorCard({required this.message, required this.onRetry});

  final String message;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            const Icon(Icons.error_outline, size: 32),
            const SizedBox(height: 8),
            Text(message, textAlign: TextAlign.center),
            const SizedBox(height: 12),
            FilledButton(onPressed: onRetry, child: const Text('Retry')),
          ],
        ),
      ),
    );
  }
}

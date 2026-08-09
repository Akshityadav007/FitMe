import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'recommendation_models.dart';
import 'recommendation_providers.dart';

class RecommendationScreen extends ConsumerWidget {
  const RecommendationScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final recommendation = ref.watch(recommendationProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Lunch suggestion')),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(recommendationProvider);
          await ref.read(recommendationProvider.future);
        },
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            recommendation.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (error, _) => _ErrorCard(
                message: error.toString(),
                onRetry: () => ref.invalidate(recommendationProvider),
              ),
              data: (data) => _RecommendationBody(data: data),
            ),
          ],
        ),
      ),
    );
  }
}

class _RecommendationBody extends StatelessWidget {
  const _RecommendationBody({required this.data});

  final Recommendation data;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Recommended', style: textTheme.titleMedium),
                const SizedBox(height: 8),
                if (data.recommendation == null)
                  Text(
                    data.uncertaintyReason ?? data.reason,
                    style: textTheme.bodyMedium,
                  )
                else
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        data.recommendation!.name,
                        style: textTheme.titleLarge,
                      ),
                      const SizedBox(height: 8),
                      Text(data.reason),
                      const SizedBox(height: 8),
                      Text(
                        '${data.recommendation!.calories} kcal · '
                        '${data.recommendation!.proteinG} g protein',
                      ),
                    ],
                  ),
                const SizedBox(height: 8),
                if (data.uncertainty)
                  Text(
                    'Note: ${data.uncertaintyReason ?? 'information is uncertain.'}',
                    style: textTheme.bodySmall,
                  ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 12),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Remaining targets', style: textTheme.titleMedium),
                const SizedBox(height: 8),
                Text('Calories: ${data.remaining.calories} kcal'),
                const SizedBox(height: 4),
                Text('Protein: ${data.remaining.proteinG} g'),
                const SizedBox(height: 4),
                Text('Carbs: ${data.remaining.carbsG} g'),
                const SizedBox(height: 4),
                Text('Fat: ${data.remaining.fatG} g'),
              ],
            ),
          ),
        ),
        if (data.alternatives.isNotEmpty) ...[
          const SizedBox(height: 12),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Alternatives', style: textTheme.titleMedium),
                  const SizedBox(height: 8),
                  for (final item in data.alternatives)
                    Padding(
                      padding: const EdgeInsets.only(bottom: 6),
                      child: Text('${item.name} — ${item.calories} kcal'),
                    ),
                ],
              ),
            ),
          ),
        ],
        const SizedBox(height: 12),
        Card(
          child: ListTile(
            leading: const Icon(Icons.chevron_right),
            title: const Text('Suggested next step'),
            subtitle: Text(data.suggestedAction),
          ),
        ),
      ],
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

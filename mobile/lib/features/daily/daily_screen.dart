import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../auth/auth_providers.dart';
import 'daily_models.dart';
import 'daily_providers.dart';

class DailyScreen extends ConsumerWidget {
  const DailyScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final summary = ref.watch(dailySummaryProvider);
    final targets = ref.watch(nutritionTargetsProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Today')),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(dailySummaryProvider);
          ref.invalidate(nutritionTargetsProvider);
          await ref.read(dailySummaryProvider.future);
        },
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            summary.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (error, _) => _ErrorCard(
                message: error.toString(),
                onRetry: () => ref.invalidate(dailySummaryProvider),
              ),
              data: (data) => _SummaryCards(summary: data, targets: targets.value),
            ),
            const SizedBox(height: 16),
            targets.when(
              loading: () => const SizedBox.shrink(),
              error: (error, _) => _ErrorCard(
                message: error.toString(),
                onRetry: () => ref.invalidate(nutritionTargetsProvider),
              ),
              data: (_) => const SizedBox.shrink(),
            ),
            _QuickActions(ref: ref),
          ],
        ),
      ),
    );
  }
}

class _SummaryCards extends StatelessWidget {
  const _SummaryCards({required this.summary, this.targets});

  final DailySummary summary;
  final NutritionTarget? targets;

  @override
  Widget build(BuildContext context) {
    final targetCalories = targets?.calories ?? 2200;
    final targetWater = targets?.waterMl ?? 2500;
    final targetProtein = targets?.proteinG ?? 150;

    return Column(
      children: [
        _MacroCard(
          calories: summary.foodCalories,
          targetCalories: targetCalories,
          protein: summary.proteinG,
          targetProtein: targetProtein,
        ),
        const SizedBox(height: 12),
        _HydrationCard(
          waterMl: summary.waterMl,
          targetWater: targetWater,
        ),
        const SizedBox(height: 12),
        _ActivityCard(
          steps: summary.steps,
          sleepMinutes: summary.sleepMinutes,
          workoutSessions: summary.workoutSessions,
          weightKg: summary.weightKg,
        ),
      ],
    );
  }
}

class _MacroCard extends StatelessWidget {
  const _MacroCard({
    required this.calories,
    required this.targetCalories,
    required this.protein,
    required this.targetProtein,
  });

  final int calories;
  final int targetCalories;
  final int protein;
  final int targetProtein;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Calories', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),
            _ProgressRow(label: 'Calories', value: calories, target: targetCalories),
            const SizedBox(height: 8),
            _ProgressRow(label: 'Protein', value: protein, target: targetProtein, suffix: 'g'),
          ],
        ),
      ),
    );
  }
}

class _ProgressRow extends StatelessWidget {
  const _ProgressRow({
    required this.label,
    required this.value,
    required this.target,
    this.suffix = 'kcal',
  });

  final String label;
  final int value;
  final int target;
  final String suffix;

  @override
  Widget build(BuildContext context) {
    final ratio = target <= 0 ? 0.0 : (value / target).clamp(0.0, 1.0);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(label),
            Text('$value / $target $suffix'),
          ],
        ),
        const SizedBox(height: 4),
        LinearProgressIndicator(value: ratio),
      ],
    );
  }
}

class _HydrationCard extends StatelessWidget {
  const _HydrationCard({required this.waterMl, required this.targetWater});

  final int waterMl;
  final int targetWater;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        leading: const Icon(Icons.water_drop),
        title: const Text('Hydration'),
        subtitle: Text('$waterMl ml of $targetWater ml'),
        trailing: const Icon(Icons.water_drop_outlined),
      ),
    );
  }
}

class _ActivityCard extends StatelessWidget {
  const _ActivityCard({
    required this.steps,
    required this.sleepMinutes,
    required this.workoutSessions,
    required this.weightKg,
  });

  final int steps;
  final int? sleepMinutes;
  final int workoutSessions;
  final double? weightKg;

  @override
  Widget build(BuildContext context) {
    final sleepMinutes = this.sleepMinutes;
    final sleep = sleepMinutes == null
        ? 'Not logged'
        : '${sleepMinutes ~/ 60}h ${sleepMinutes % 60}m';
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Activity', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),
            _DetailRow(icon: Icons.directions_walk, label: 'Steps', value: '$steps'),
            const SizedBox(height: 6),
            _DetailRow(icon: Icons.bedtime, label: 'Sleep', value: sleep),
            const SizedBox(height: 6),
            _DetailRow(icon: Icons.fitness_center, label: 'Workouts', value: '$workoutSessions'),
            if (weightKg != null) ...[
              const SizedBox(height: 6),
              _DetailRow(icon: Icons.monitor_weight, label: 'Weight', value: '$weightKg kg'),
            ],
          ],
        ),
      ),
    );
  }
}

class _DetailRow extends StatelessWidget {
  const _DetailRow({required this.icon, required this.label, required this.value});

  final IconData icon;
  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(icon, size: 18),
        const SizedBox(width: 8),
        Text('$label: $value'),
      ],
    );
  }
}

class _QuickActions extends ConsumerWidget {
  const _QuickActions({required this.ref});

  final WidgetRef ref;

  Future<void> _refresh(BuildContext context) async {
    ref.invalidate(dailySummaryProvider);
    ref.invalidate(nutritionTargetsProvider);
    if (context.mounted) {
      await ref.read(dailySummaryProvider.future);
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef widgetRef) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Quick log', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: FilledButton.icon(
                    onPressed: () async {
                      await ref.read(logWaterProvider(250).future);
                      if (context.mounted) {
                        await _refresh(context);
                      }
                    },
                    icon: const Icon(Icons.water_drop),
                    label: const Text('+250 ml'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () async {
                      await ref.read(logWaterProvider(500).future);
                      if (context.mounted) {
                        await _refresh(context);
                      }
                    },
                    icon: const Icon(Icons.water_drop),
                    label: const Text('+500 ml'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: _LogActionButton(
                    icon: Icons.set_meal,
                    label: 'Food',
                    onPressed: () => _showFoodDialog(context),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: _LogActionButton(
                    icon: Icons.directions_walk,
                    label: 'Steps',
                    onPressed: () => _showStepsDialog(context),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: _LogActionButton(
                    icon: Icons.bedtime,
                    label: 'Sleep',
                    onPressed: () => _showSleepDialog(context),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: _LogActionButton(
                    icon: Icons.fitness_center,
                    label: 'Workout',
                    onPressed: () => _showWorkoutDialog(context),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: _LogActionButton(
                    icon: Icons.monitor_weight,
                    label: 'Weight',
                    onPressed: () => _showWeightDialog(context),
                  ),
                ),
                const SizedBox(width: 8),
                const Expanded(child: SizedBox.shrink()),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _showFoodDialog(BuildContext context) async {
    final result = await showDialog<Map<String, String>>(
      context: context,
      builder: (context) => const _FoodEntryDialog(),
    );
    if (result == null) {
      return;
    }
    final token = ref.read(authTokenProvider).value;
    if (token == null) {
      return;
    }
    final date = DateTime.now().toIso8601String().substring(0, 10);
    await ref.read(dailyRepositoryProvider).logFood(
          token: token,
          date: date,
          mealType: result['meal_type']!,
          foodName: result['food_name']!,
          calories: int.tryParse(result['calories']!) ?? 0,
          proteinG: int.tryParse(result['protein_g']!) ?? 0,
          carbsG: int.tryParse(result['carbs_g']!) ?? 0,
          fatG: int.tryParse(result['fat_g']!) ?? 0,
        );
    if (context.mounted) {
      await _refresh(context);
    }
  }

  Future<void> _showStepsDialog(BuildContext context) async {
    final controller = TextEditingController();
    final result = await showDialog<int>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Log steps'),
        content: TextField(
          controller: controller,
          keyboardType: TextInputType.number,
          decoration: const InputDecoration(labelText: 'Steps'),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, int.tryParse(controller.text.trim()) ?? 0),
            child: const Text('Save'),
          ),
        ],
      ),
    );
    if (result == null || result <= 0) {
      return;
    }
    await ref.read(logStepsProvider(result).future);
    if (context.mounted) {
      await _refresh(context);
    }
  }

  Future<void> _showSleepDialog(BuildContext context) async {
    final controller = TextEditingController();
    final result = await showDialog<int>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Log sleep'),
        content: TextField(
          controller: controller,
          keyboardType: TextInputType.number,
          decoration: const InputDecoration(labelText: 'Minutes slept'),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, int.tryParse(controller.text.trim()) ?? 0),
            child: const Text('Save'),
          ),
        ],
      ),
    );
    if (result == null || result <= 0) {
      return;
    }
    await ref.read(logSleepProvider(result).future);
    if (context.mounted) {
      await _refresh(context);
    }
  }

  Future<void> _showWorkoutDialog(BuildContext context) async {
    final nameController = TextEditingController();
    final minutesController = TextEditingController();
    final result = await showDialog<({String name, int? minutes})>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Log workout'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: nameController,
              decoration: const InputDecoration(labelText: 'Workout name'),
            ),
            TextField(
              controller: minutesController,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(labelText: 'Duration (minutes)'),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(
              context,
              (
                name: nameController.text.trim(),
                minutes: int.tryParse(minutesController.text.trim()),
              ),
            ),
            child: const Text('Save'),
          ),
        ],
      ),
    );
    if (result == null || result.name.isEmpty) {
      return;
    }
    await ref.read(logWorkoutProvider((name: result.name, durationMinutes: result.minutes)).future);
    if (context.mounted) {
      await _refresh(context);
    }
  }

  Future<void> _showWeightDialog(BuildContext context) async {
    final controller = TextEditingController();
    final result = await showDialog<double>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Log weight'),
        content: TextField(
          controller: controller,
          keyboardType: const TextInputType.numberWithOptions(decimal: true),
          decoration: const InputDecoration(labelText: 'Weight (kg)'),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, double.tryParse(controller.text.trim()) ?? 0),
            child: const Text('Save'),
          ),
        ],
      ),
    );
    if (result == null || result <= 0) {
      return;
    }
    final token = ref.read(authTokenProvider).value;
    if (token == null) {
      return;
    }
    final date = DateTime.now().toIso8601String().substring(0, 10);
    await ref.read(dailyRepositoryProvider).logWeight(
          token: token,
          date: date,
          weightKg: result,
        );
    if (context.mounted) {
      await _refresh(context);
    }
  }
}

class _LogActionButton extends StatelessWidget {
  const _LogActionButton({required this.icon, required this.label, required this.onPressed});

  final IconData icon;
  final String label;
  final VoidCallback onPressed;

  @override
  Widget build(BuildContext context) {
    return OutlinedButton.icon(
      onPressed: onPressed,
      icon: Icon(icon),
      label: Text(label),
    );
  }
}

class _FoodEntryDialog extends StatefulWidget {
  const _FoodEntryDialog();

  @override
  State<_FoodEntryDialog> createState() => _FoodEntryDialogState();
}

class _FoodEntryDialogState extends State<_FoodEntryDialog> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _caloriesController = TextEditingController();
  final _proteinController = TextEditingController();
  final _carbsController = TextEditingController();
  final _fatController = TextEditingController();
  String _mealType = 'meal';

  @override
  void dispose() {
    _nameController.dispose();
    _caloriesController.dispose();
    _proteinController.dispose();
    _carbsController.dispose();
    _fatController.dispose();
    super.dispose();
  }

  void _submit() {
    if (_formKey.currentState!.validate()) {
      Navigator.pop(context, {
        'meal_type': _mealType,
        'food_name': _nameController.text.trim(),
        'calories': _caloriesController.text.trim(),
        'protein_g': _proteinController.text.trim(),
        'carbs_g': _carbsController.text.trim(),
        'fat_g': _fatController.text.trim(),
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Log food'),
      content: SingleChildScrollView(
        child: Form(
          key: _formKey,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextFormField(
                controller: _nameController,
                decoration: const InputDecoration(labelText: 'Food name'),
                validator: (value) => (value == null || value.trim().isEmpty)
                    ? 'Enter a food name.'
                    : null,
              ),
              DropdownButtonFormField<String>(
                initialValue: _mealType,
                decoration: const InputDecoration(labelText: 'Meal'),
                items: const [
                  DropdownMenuItem(value: 'breakfast', child: Text('Breakfast')),
                  DropdownMenuItem(value: 'lunch', child: Text('Lunch')),
                  DropdownMenuItem(value: 'dinner', child: Text('Dinner')),
                  DropdownMenuItem(value: 'snack', child: Text('Snack')),
                  DropdownMenuItem(value: 'meal', child: Text('Meal')),
                ],
                onChanged: (value) => setState(() => _mealType = value ?? 'meal'),
              ),
              _MacroField(controller: _caloriesController, label: 'Calories'),
              _MacroField(controller: _proteinController, label: 'Protein (g)'),
              _MacroField(controller: _carbsController, label: 'Carbs (g)'),
              _MacroField(controller: _fatController, label: 'Fat (g)'),
            ],
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Cancel'),
        ),
        FilledButton(onPressed: _submit, child: const Text('Save')),
      ],
    );
  }
}

class _MacroField extends StatelessWidget {
  const _MacroField({required this.controller, required this.label});

  final TextEditingController controller;
  final String label;

  @override
  Widget build(BuildContext context) {
    return TextFormField(
      controller: controller,
      keyboardType: TextInputType.number,
      decoration: InputDecoration(labelText: label),
      validator: (value) {
        final parsed = int.tryParse((value ?? '').trim());
        if (parsed == null || parsed < 0) {
          return 'Enter a non-negative number.';
        }
        return null;
      },
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

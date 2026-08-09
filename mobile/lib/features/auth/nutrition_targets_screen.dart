import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../daily/daily_models.dart';
import '../daily/daily_providers.dart';
import 'auth_providers.dart';

class NutritionTargetsScreen extends ConsumerStatefulWidget {
  const NutritionTargetsScreen({super.key});

  @override
  ConsumerState<NutritionTargetsScreen> createState() => _NutritionTargetsScreenState();
}

class _NutritionTargetsScreenState extends ConsumerState<NutritionTargetsScreen> {
  final _formKey = GlobalKey<FormState>();
  final _caloriesController = TextEditingController();
  final _proteinController = TextEditingController();
  final _carbsController = TextEditingController();
  final _fatController = TextEditingController();
  final _waterController = TextEditingController();
  final _fiberController = TextEditingController();
  final _sodiumController = TextEditingController();
  bool _submitting = false;
  bool _hydrated = false;
  String? _error;

  @override
  void dispose() {
    _caloriesController.dispose();
    _proteinController.dispose();
    _carbsController.dispose();
    _fatController.dispose();
    _waterController.dispose();
    _fiberController.dispose();
    _sodiumController.dispose();
    super.dispose();
  }

  void _hydrate(NutritionTarget targets) {
    if (_hydrated) {
      return;
    }
    _hydrated = true;
    _caloriesController.text = targets.calories.toString();
    _proteinController.text = targets.proteinG.toString();
    _carbsController.text = targets.carbsG.toString();
    _fatController.text = targets.fatG.toString();
    _waterController.text = targets.waterMl.toString();
    _fiberController.text = targets.fiberG.toString();
    _sodiumController.text = targets.sodiumMg.toString();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }
    final token = ref.read(authTokenProvider).value;
    if (token == null) {
      return;
    }
    setState(() {
      _submitting = true;
      _error = null;
    });
    final payload = <String, dynamic>{
      'calories': int.parse(_caloriesController.text),
      'protein_g': int.parse(_proteinController.text),
      'carbs_g': int.parse(_carbsController.text),
      'fat_g': int.parse(_fatController.text),
      'water_ml': int.parse(_waterController.text),
      'fiber_g': int.parse(_fiberController.text),
      'sodium_mg': int.parse(_sodiumController.text),
    };
    try {
      await ref.read(authRepositoryProvider).updateNutritionTargets(token, payload);
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(const SnackBar(content: Text('Targets saved.')));
      }
      ref.invalidate(nutritionTargetsProvider);
    } catch (error) {
      setState(() => _error = error.toString());
    } finally {
      if (mounted) {
        setState(() => _submitting = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final targets = ref.watch(nutritionTargetsProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Nutrition targets')),
      body: targets.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => Center(child: Text(error.toString())),
        data: (data) {
          _hydrate(data);
          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  _NumberField(controller: _caloriesController, label: 'Calories (kcal)', helper: 'Daily calorie target'),
                  _NumberField(controller: _proteinController, label: 'Protein (g)'),
                  _NumberField(controller: _carbsController, label: 'Carbs (g)'),
                  _NumberField(controller: _fatController, label: 'Fat (g)'),
                  _NumberField(controller: _waterController, label: 'Water (ml)'),
                  _NumberField(controller: _fiberController, label: 'Fiber (g)'),
                  _NumberField(controller: _sodiumController, label: 'Sodium (mg)'),
                  if (_error != null) ...[
                    const SizedBox(height: 12),
                    Text(_error!, style: TextStyle(color: Theme.of(context).colorScheme.error)),
                  ],
                  const SizedBox(height: 24),
                  FilledButton(
                    onPressed: _submitting ? null : _submit,
                    child: _submitting
                        ? const SizedBox(
                            height: 18,
                            width: 18,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Text('Save targets'),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}

class _NumberField extends StatelessWidget {
  const _NumberField({required this.controller, required this.label, this.helper});

  final TextEditingController controller;
  final String label;
  final String? helper;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: TextFormField(
        controller: controller,
        keyboardType: TextInputType.number,
        decoration: InputDecoration(labelText: label, helperText: helper),
        validator: (value) {
          final parsed = int.tryParse((value ?? '').trim());
          if (parsed == null || parsed < 0) {
            return 'Enter a non-negative number.';
          }
          return null;
        },
      ),
    );
  }
}

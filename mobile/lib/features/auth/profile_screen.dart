import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'auth_models.dart';
import 'auth_providers.dart';

class ProfileScreen extends ConsumerStatefulWidget {
  const ProfileScreen({super.key});

  @override
  ConsumerState<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends ConsumerState<ProfileScreen> {
  final _formKey = GlobalKey<FormState>();
  final _firstNameController = TextEditingController();
  final _lastNameController = TextEditingController();
  final _ageController = TextEditingController();
  final _sexController = TextEditingController();
  final _weightController = TextEditingController();
  final _heightController = TextEditingController();
  final _goalController = TextEditingController();
  final _activityController = TextEditingController();
  final _dietaryController = TextEditingController();
  final _notesController = TextEditingController();
  bool _submitting = false;
  bool _hydrated = false;
  String? _error;

  @override
  void dispose() {
    _firstNameController.dispose();
    _lastNameController.dispose();
    _ageController.dispose();
    _sexController.dispose();
    _weightController.dispose();
    _heightController.dispose();
    _goalController.dispose();
    _activityController.dispose();
    _dietaryController.dispose();
    _notesController.dispose();
    super.dispose();
  }

  void _hydrate(UserProfile profile) {
    if (_hydrated) {
      return;
    }
    _hydrated = true;
    _firstNameController.text = profile.firstName ?? '';
    _lastNameController.text = profile.lastName ?? '';
    _ageController.text = profile.age?.toString() ?? '';
    _sexController.text = profile.sex ?? '';
    _weightController.text = profile.weightKg?.toString() ?? '';
    _heightController.text = profile.heightCm?.toString() ?? '';
    _goalController.text = profile.goal ?? '';
    _activityController.text = profile.activityLevel ?? '';
    _dietaryController.text = profile.dietaryPreferences ?? '';
    _notesController.text = profile.notes ?? '';
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
      'first_name': _emptyToNull(_firstNameController.text),
      'last_name': _emptyToNull(_lastNameController.text),
      'age': _emptyToNull(_ageController.text) == null
          ? null
          : int.tryParse(_ageController.text),
      'sex': _emptyToNull(_sexController.text),
      'weight_kg': _emptyToNull(_weightController.text) == null
          ? null
          : double.tryParse(_weightController.text),
      'height_cm': _emptyToNull(_heightController.text) == null
          ? null
          : double.tryParse(_heightController.text),
      'goal': _emptyToNull(_goalController.text),
      'activity_level': _emptyToNull(_activityController.text),
      'dietary_preferences': _emptyToNull(_dietaryController.text),
      'notes': _emptyToNull(_notesController.text),
    };
    try {
      await ref.read(authRepositoryProvider).updateProfile(token, payload);
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(const SnackBar(content: Text('Profile saved.')));
      }
      ref.invalidate(profileProvider);
    } catch (error) {
      setState(() => _error = error.toString());
    } finally {
      if (mounted) {
        setState(() => _submitting = false);
      }
    }
  }

  String? _emptyToNull(String value) {
    final trimmed = value.trim();
    return trimmed.isEmpty ? null : trimmed;
  }

  @override
  Widget build(BuildContext context) {
    final profile = ref.watch(profileProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Profile'),
        actions: [
          IconButton(
            tooltip: 'Sign out',
            icon: const Icon(Icons.logout),
            onPressed: () async {
              await ref.read(authRepositoryProvider).signOut();
              ref.invalidate(authTokenProvider);
            },
          ),
        ],
      ),
      body: profile.when(
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
                  TextFormField(
                    controller: _firstNameController,
                    decoration: const InputDecoration(labelText: 'First name'),
                  ),
                  TextFormField(
                    controller: _lastNameController,
                    decoration: const InputDecoration(labelText: 'Last name'),
                  ),
                  TextFormField(
                    controller: _ageController,
                    decoration: const InputDecoration(labelText: 'Age'),
                    keyboardType: TextInputType.number,
                  ),
                  TextFormField(
                    controller: _sexController,
                    decoration: const InputDecoration(labelText: 'Sex'),
                  ),
                  TextFormField(
                    controller: _weightController,
                    decoration: const InputDecoration(labelText: 'Weight (kg)'),
                    keyboardType: TextInputType.number,
                  ),
                  TextFormField(
                    controller: _heightController,
                    decoration: const InputDecoration(labelText: 'Height (cm)'),
                    keyboardType: TextInputType.number,
                  ),
                  TextFormField(
                    controller: _goalController,
                    decoration: const InputDecoration(labelText: 'Goal'),
                  ),
                  TextFormField(
                    controller: _activityController,
                    decoration: const InputDecoration(labelText: 'Activity level'),
                  ),
                  TextFormField(
                    controller: _dietaryController,
                    decoration: const InputDecoration(labelText: 'Dietary preferences'),
                  ),
                  TextFormField(
                    controller: _notesController,
                    decoration: const InputDecoration(labelText: 'Notes'),
                    maxLines: 3,
                  ),
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
                        : const Text('Save profile'),
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

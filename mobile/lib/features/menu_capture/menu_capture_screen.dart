import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';

import '../auth/auth_providers.dart';
import '../daily/daily_providers.dart';
import 'menu_models.dart';
import 'menu_providers.dart';

class MenuCaptureScreen extends ConsumerWidget {
  const MenuCaptureScreen({super.key});

  Future<void> _pickAndUpload(BuildContext context, WidgetRef ref, ImageSource source) async {
    final messenger = ScaffoldMessenger.of(context);
    final picker = ImagePicker();
    final picked = await picker.pickImage(source: source, maxWidth: 1600, maxHeight: 1600);
    if (picked == null) {
      return;
    }
    final bytes = await picked.readAsBytes();
    final contentType = picked.mimeType ?? 'image/jpeg';
    await ref
        .read(menuCaptureControllerProvider.notifier)
        .uploadAndProcess(bytes: bytes, contentType: contentType);
    if (ref.read(menuCaptureControllerProvider).status == MenuCaptureStatus.error) {
      messenger.showSnackBar(
        SnackBar(content: Text(ref.read(menuCaptureControllerProvider).error!)),
      );
    }
  }

  Future<void> _confirm(BuildContext context, WidgetRef ref, MenuImageItem item) async {
    final messenger = ScaffoldMessenger.of(context);
    final token = ref.read(authTokenProvider).value;
    if (token == null) {
      return;
    }
    final date = DateTime.now().toIso8601String().substring(0, 10);
    try {
      await ref.read(menuCaptureRepositoryProvider).confirmItem(
            token: token,
            menuItemId: item.id,
            date: date,
            mealType: 'lunch',
            quantityG: 100,
          );
      messenger.showSnackBar(SnackBar(content: Text('${item.name} logged.')));
      ref.invalidate(dailySummaryProvider);
    } catch (error) {
      messenger.showSnackBar(SnackBar(content: Text(error.toString())));
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(menuCaptureControllerProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Capture menu')),
      body: switch (state.status) {
        MenuCaptureStatus.idle => _IdleView(onCamera: () => _pickAndUpload(context, ref, ImageSource.camera), onGallery: () => _pickAndUpload(context, ref, ImageSource.gallery)),
        MenuCaptureStatus.uploading => const _BusyView(label: 'Uploading photo…'),
        MenuCaptureStatus.processing => const _BusyView(label: 'Extracting menu items…'),
        MenuCaptureStatus.error => _ErrorView(message: state.error!, onRetry: () => ref.read(menuCaptureControllerProvider.notifier).reset()),
        MenuCaptureStatus.done => _ResultsView(
            items: state.items,
            onConfirm: (item) => _confirm(context, ref, item),
            onNew: () => ref.read(menuCaptureControllerProvider.notifier).reset(),
          ),
      },
    );
  }
}

class _IdleView extends StatelessWidget {
  const _IdleView({required this.onCamera, required this.onGallery});

  final VoidCallback onCamera;
  final VoidCallback onGallery;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.photo_camera, size: 64),
            const SizedBox(height: 16),
            Text(
              'Photograph the office menu to extract the available dishes.',
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),
            FilledButton.icon(
              onPressed: onCamera,
              icon: const Icon(Icons.photo_camera),
              label: const Text('Take a photo'),
            ),
            const SizedBox(height: 12),
            OutlinedButton.icon(
              onPressed: onGallery,
              icon: const Icon(Icons.photo_library),
              label: const Text('Choose from gallery'),
            ),
          ],
        ),
      ),
    );
  }
}

class _BusyView extends StatelessWidget {
  const _BusyView({required this.label});

  final String label;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const CircularProgressIndicator(),
          const SizedBox(height: 16),
          Text(label),
        ],
      ),
    );
  }
}

class _ErrorView extends StatelessWidget {
  const _ErrorView({required this.message, required this.onRetry});

  final String message;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.error_outline, size: 40),
            const SizedBox(height: 12),
            Text(message, textAlign: TextAlign.center),
            const SizedBox(height: 16),
            FilledButton(onPressed: onRetry, child: const Text('Try again')),
          ],
        ),
      ),
    );
  }
}

class _ResultsView extends StatelessWidget {
  const _ResultsView({required this.items, required this.onConfirm, required this.onNew});

  final List<MenuImageItem> items;
  final ValueChanged<MenuImageItem> onConfirm;
  final VoidCallback onNew;

  @override
  Widget build(BuildContext context) {
    if (items.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.no_meals, size: 40),
              const SizedBox(height: 12),
              const Text('No menu items could be read from the photo.'),
              const SizedBox(height: 16),
              FilledButton(onPressed: onNew, child: const Text('Try another photo')),
            ],
          ),
        ),
      );
    }
    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.all(16),
          child: Text(
            '${items.length} item(s) detected. Tap one to log it for today’s lunch.',
            textAlign: TextAlign.center,
          ),
        ),
        Expanded(
          child: ListView.separated(
            itemCount: items.length,
            separatorBuilder: (context, index) => const Divider(height: 1),
            itemBuilder: (context, index) {
              final item = items[index];
              return ListTile(
                leading: const Icon(Icons.restaurant),
                title: Text(item.name),
                subtitle: Text(
                  '${item.estimatedCalories} kcal · P ${item.estimatedProteinG}g '
                  '· C ${item.estimatedCarbsG}g · F ${item.estimatedFatG}g',
                ),
                trailing: const Icon(Icons.add_circle_outline),
                onTap: () => onConfirm(item),
              );
            },
          ),
        ),
        SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: OutlinedButton.icon(
              onPressed: onNew,
              icon: const Icon(Icons.refresh),
              label: const Text('Capture another menu'),
            ),
          ),
        ),
      ],
    );
  }
}

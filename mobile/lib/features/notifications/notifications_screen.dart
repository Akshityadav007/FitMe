import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../auth/auth_providers.dart';
import 'notification_models.dart';
import 'notification_providers.dart';

class NotificationsScreen extends ConsumerWidget {
  const NotificationsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final notifications = ref.watch(notificationsProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Notifications'),
        actions: [
          IconButton(
            tooltip: 'Check for new notifications',
            icon: const Icon(Icons.refresh),
            onPressed: () async {
              final token = ref.read(authTokenProvider).value;
              if (token == null) {
                return;
              }
              await ref.read(notificationRepositoryProvider).check(token: token);
              ref.invalidate(notificationsProvider);
            },
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(notificationsProvider);
          await ref.read(notificationsProvider.future);
        },
        child: notifications.when(
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (error, _) => Center(
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Icon(Icons.error_outline, size: 32),
                  const SizedBox(height: 8),
                  Text(error.toString(), textAlign: TextAlign.center),
                  const SizedBox(height: 12),
                  FilledButton(
                    onPressed: () => ref.invalidate(notificationsProvider),
                    child: const Text('Retry'),
                  ),
                ],
              ),
            ),
          ),
          data: (items) {
            if (items.isEmpty) {
              return const Center(child: Text('No notifications yet.'));
            }
            return ListView.separated(
              itemCount: items.length,
              separatorBuilder: (context, index) => const Divider(height: 1),
              itemBuilder: (context, index) =>
                  _NotificationTile(item: items[index], onTap: () async {
                    if (items[index].readAt == null) {
                      await ref
                          .read(notificationRepositoryProvider)
                          .markRead(
                            token: ref.read(authTokenProvider).value!,
                            notificationId: items[index].id,
                          );
                      ref.invalidate(notificationsProvider);
                    }
                  }),
            );
          },
        ),
      ),
    );
  }
}

class _NotificationTile extends StatelessWidget {
  const _NotificationTile({required this.item, required this.onTap});

  final NotificationItem item;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final isUnread = item.readAt == null;
    return ListTile(
      leading: Icon(
        switch (item.category) {
          'hydration' => Icons.water_drop,
          'protein' => Icons.set_meal,
          'meal' => Icons.restaurant,
          'end_of_day' => Icons.nights_stay,
          _ => Icons.notifications,
        },
      ),
      title: Text(
        item.title,
        style: TextStyle(fontWeight: isUnread ? FontWeight.bold : FontWeight.normal),
      ),
      subtitle: Text(item.body),
      isThreeLine: true,
      onTap: onTap,
    );
  }
}

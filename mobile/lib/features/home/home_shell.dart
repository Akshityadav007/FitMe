import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../auth/auth_providers.dart';
import '../auth/auth_screen.dart';
import '../auth/nutrition_targets_screen.dart';
import '../auth/profile_screen.dart';
import '../coach/coach_screen.dart';
import '../daily/daily_screen.dart';
import '../menu_capture/menu_capture_screen.dart';
import '../notifications/notifications_screen.dart';
import '../progress/progress_screen.dart';
import '../recommendation/recommendation_screen.dart';

class HomeShell extends ConsumerStatefulWidget {
  const HomeShell({super.key});

  @override
  ConsumerState<HomeShell> createState() => _HomeShellState();
}

class _HomeShellState extends ConsumerState<HomeShell> {
  int _index = 0;

  @override
  Widget build(BuildContext context) {
    final token = ref.watch(authTokenProvider);
    return token.when(
      loading: () => const Scaffold(body: Center(child: CircularProgressIndicator())),
      error: (error, _) => AuthScreen(),
      data: (value) {
        if (value == null) {
          return const AuthScreen();
        }
        return _buildShell();
      },
    );
  }

  Widget _buildShell() {
    final screens = [
      const DailyScreen(),
      const RecommendationScreen(),
      const CoachScreen(),
      const ProgressScreen(),
      const MenuCaptureScreen(),
      const NotificationsScreen(),
      const ProfileScreen(),
      const NutritionTargetsScreen(),
    ];
    return Scaffold(
      body: IndexedStack(index: _index, children: screens),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _index,
        onDestinationSelected: (index) => setState(() => _index = index),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.today), label: 'Today'),
          NavigationDestination(icon: Icon(Icons.restaurant), label: 'Suggest'),
          NavigationDestination(icon: Icon(Icons.support_agent), label: 'Coach'),
          NavigationDestination(icon: Icon(Icons.insert_chart), label: 'Progress'),
          NavigationDestination(icon: Icon(Icons.photo_camera), label: 'Menu'),
          NavigationDestination(icon: Icon(Icons.notifications), label: 'Alerts'),
          NavigationDestination(icon: Icon(Icons.person), label: 'Profile'),
          NavigationDestination(icon: Icon(Icons.track_changes), label: 'Targets'),
        ],
      ),
    );
  }
}

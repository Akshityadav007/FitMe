import 'package:flutter/material.dart';

import 'features/home/home_shell.dart';

class FitMeApp extends StatelessWidget {
  const FitMeApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'FitMe',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF256D5A)),
        useMaterial3: true,
      ),
      home: const HomeShell(),
    );
  }
}

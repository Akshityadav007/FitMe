import 'package:fitme/app.dart';
import 'package:fitme/features/auth/auth_providers.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

void main() {
  testWidgets('renders the application shell', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          authTokenProvider.overrideWith((ref) async => null),
        ],
        child: const FitMeApp(),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('FitMe'), findsOneWidget);
  });
}

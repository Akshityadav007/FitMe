import 'package:fitme/app.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

void main() {
  testWidgets('renders the application shell', (tester) async {
    await tester.pumpWidget(const ProviderScope(child: FitMeApp()));

    expect(find.text('FitMe'), findsOneWidget);
  });
}

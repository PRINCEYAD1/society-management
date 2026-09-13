import 'package:flutter_test/flutter_test.dart';
import 'package:society_mobile/main.dart';

void main() {
  testWidgets('Society Management app loads', (WidgetTester tester) async {
    await tester.pumpWidget(const SocietyApp());

    expect(find.text('Society Management Login'), findsOneWidget);
  });
}
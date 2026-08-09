class AppConfig {
  const AppConfig({required this.apiBaseUrl});

  static const fromEnvironment = AppConfig(
    apiBaseUrl: String.fromEnvironment(
      'FITME_API_BASE_URL',
      defaultValue: 'http://localhost:8000/api/v1',
    ),
  );

  final String apiBaseUrl;
}

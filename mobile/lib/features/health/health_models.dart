class HealthResponse {
  const HealthResponse({
    required this.status,
    required this.service,
    required this.checkedAt,
  });

  factory HealthResponse.fromJson(Map<String, Object?> json) {
    return HealthResponse(
      status: json['status'] as String,
      service: json['service'] as String,
      checkedAt: DateTime.parse(json['checked_at'] as String),
    );
  }

  final String status;
  final String service;
  final DateTime checkedAt;
}

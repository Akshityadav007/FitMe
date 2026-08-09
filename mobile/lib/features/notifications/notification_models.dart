class NotificationItem {
  const NotificationItem({
    required this.id,
    required this.userId,
    required this.category,
    required this.title,
    required this.body,
    required this.createdAt,
    this.readAt,
  });

  factory NotificationItem.fromJson(Map<String, Object?> json) {
    return NotificationItem(
      id: json['id'] as String,
      userId: json['user_id'] as String,
      category: json['category'] as String,
      title: json['title'] as String,
      body: json['body'] as String,
      createdAt: DateTime.parse(json['created_at'] as String),
      readAt: json['read_at'] == null ? null : DateTime.parse(json['read_at'] as String),
    );
  }

  final String id;
  final String userId;
  final String category;
  final String title;
  final String body;
  final DateTime createdAt;
  final DateTime? readAt;
}

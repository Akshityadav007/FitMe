class CoachMessage {
  const CoachMessage({required this.role, required this.content});

  factory CoachMessage.fromJson(Map<String, Object?> json) {
    return CoachMessage(
      role: json['role'] as String,
      content: json['content'] as String,
    );
  }

  final String role;
  final String content;
}

class CoachChatResponse {
  const CoachChatResponse({
    required this.conversationId,
    required this.reply,
    this.recommendation,
    this.reason,
    this.remainingCalories,
    this.remainingProteinG,
    this.uncertainty = false,
    this.uncertaintyReason,
    this.suggestedAction,
    this.messages = const [],
  });

  factory CoachChatResponse.fromJson(Map<String, Object?> json) {
    final rawMessages = json['messages'] as List<Object?>? ?? const [];
    return CoachChatResponse(
      conversationId: json['conversation_id'] as String,
      reply: json['reply'] as String,
      recommendation: json['recommendation'] as String?,
      reason: json['reason'] as String?,
      remainingCalories: json['remaining_calories'] as int?,
      remainingProteinG: json['remaining_protein_g'] as int?,
      uncertainty: (json['uncertainty'] as bool?) ?? false,
      uncertaintyReason: json['uncertainty_reason'] as String?,
      suggestedAction: json['suggested_action'] as String?,
      messages: rawMessages
          .map((message) => CoachMessage.fromJson(message as Map<String, Object?>))
          .toList(),
    );
  }

  final String conversationId;
  final String reply;
  final String? recommendation;
  final String? reason;
  final int? remainingCalories;
  final int? remainingProteinG;
  final bool uncertainty;
  final String? uncertaintyReason;
  final String? suggestedAction;
  final List<CoachMessage> messages;
}

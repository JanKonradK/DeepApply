export interface InteractionLog {
    id: string;
    applicationId: string;
    timestamp: Date;
    type: 'EMAIL_RECEIVED' | 'STATUS_CHANGE' | 'INTERVIEW_SCHEDULED' | 'NOTE_ADDED' | 'AUTO_REPLY';
    content: string; // JSON string or plain text
    sentiment?: 'POSITIVE' | 'NEGATIVE' | 'NEUTRAL';
    responseTimeMs?: number; // Time since application submission
    metadata?: Record<string, any>;
}

export interface ApplicationLifecycle {
    id: string;
    jobId: string;
    status: 'DISCOVERED' | 'APPLIED' | 'INTERVIEWING' | 'OFFER' | 'REJECTED' | 'GHOSTED';
    appliedAt?: Date;
    lastInteractionAt?: Date;
    interactions: InteractionLog[];
}

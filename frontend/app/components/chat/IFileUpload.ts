export const enum MessageType {
    USER = "user",
    SERVER = "server"
}

export interface MessagePayload {
    text: string | null;
    filename: string | null;
}

export interface ChatHistory {
    message: string;
    type: MessageType;
}
// Assuming this is the definition of the Message type
export interface Message {
    text?: string;
    sender: "user" | "bot";
    imageBase64?: string; // Optional property for the image
  }
  
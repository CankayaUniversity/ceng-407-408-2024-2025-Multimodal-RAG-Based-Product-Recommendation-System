export interface Message {
  text: string;
  sender: "user" | "bot";
  imageBase64?: string;
  category?: string;
  imageUrls?: string[]; // ← new
}

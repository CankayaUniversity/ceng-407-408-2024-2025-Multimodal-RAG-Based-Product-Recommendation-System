export interface Message{
    text?: string;
    image_url?:string;
    sender: "user" | "bot";
    
}
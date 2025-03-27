export const sendMessageToBackend = async (message: string, image: string | undefined): Promise<string> => {
  try {
    let responseText = "";

    // 1. If there is a text message
    if (message.trim()) {
      const textResponse = await fetch("http://localhost:3001/test", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });

      const data = await textResponse.json();
      responseText = data.response;
    }

    // 2. If there is an image
    if (image) {
      const imageData = { imageBase64: image };

      const fileResponse = await fetch("http://localhost:3001/upload", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(imageData),
      });

      const fileData = await fileResponse.json();
      if (fileData.success) {
        responseText = "Image uploaded successfully!";
      } else {
        responseText = "Error: Image upload failed.";
      }
    }

    return responseText;
  } catch (error) {
    console.error("Error communicating with backend:", error);
    return "Error: Unable to reach the server.";
  }
};

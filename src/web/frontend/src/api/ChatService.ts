export const sendMessageToBackend = async (
  message: string,
  image: string | undefined,
  token: string | null,
  category: string, // Added category parameter
  email: string | null
): Promise<string> => {
  try {
    const payload = {
      message: message.trim() || null,
      imageBase64: image || null,
      category: category || null,
      email: email || null
    };

    const response = await fetch("http://localhost:3001/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (response.ok) {
      return data.response || "Success!";
    } else {
      return `Error: ${data.error || "Request failed"}`;
    }
  } catch (error) {
    console.error("Error communicating with backend:", error);
    return "Error: Unable to reach the server.";
  }
};

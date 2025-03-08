export const sendMessageToBackend = async (message: string): Promise<string> => {
    try {
      const response = await fetch("http://localhost:3001/test", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });
  
      const data = await response.json();
      return data.response;
    } catch (error) {
      console.error("Error communicating with backend:", error);
      return "Error: Unable to reach the server.";
    }
  };
  
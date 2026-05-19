import { getApiUrl } from "./api-config";

export async function askQuestion(
  question: string
) {
  const API_URL = getApiUrl();
  const response = await fetch(
    `${API_URL}/api/query`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        question,
      }),
    }
  );

  console.log("API response:", response);

  if (!response.ok) {
    throw new Error(
      "Failed to fetch response"
    );
  }

  return response.json();
}

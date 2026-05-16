const API_URL =
  process.env.NEXT_PUBLIC_API_URL;

export async function askQuestion(
  question: string
) {
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

  if (!response.ok) {
    throw new Error(
      "Failed to fetch response"
    );
  }

  return response.json();
}
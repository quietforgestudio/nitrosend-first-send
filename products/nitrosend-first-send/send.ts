// One transactional email sent with the Nitrosend TypeScript SDK.
// Quietforge Studio — an AI-run studio. Compiled with tsc --strict, run on Node.
// The API key is read from the environment and never from a file.
import { Nitrosend } from "@nitrosend/sdk";

const apiKey: string | undefined = process.env.NITROSEND_API_KEY;
if (!apiKey) {
  throw new Error("NITROSEND_API_KEY is not set in the environment");
}

const ns = new Nitrosend(apiKey);

async function main(): Promise<void> {
  const res = await ns.messages.send(
    {
      channel: "email",
      to: "proof@dogfood.nitrosend.net",
      subject: "Quietforge SDK first send",
      html: "<p>First send from the Nitrosend TypeScript SDK 0.11.6,"
        + " by Quietforge Studio, an AI-run studio.</p>",
    },
    "qf-sdk-send-2",
  );
  console.log(JSON.stringify(res, null, 2));
}

main().catch((err: unknown) => {
  console.error(err);
  process.exit(1);
});

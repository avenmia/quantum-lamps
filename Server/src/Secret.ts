import * as dotenv from "dotenv";
dotenv.config();
const SharedSecret = process.env.SHARED_SECRET;
if (!SharedSecret)
{
  console.error("Set the SHARED_SECRET environment variable");
  process.exit(1);
}
export default SharedSecret;
import { VlrClient } from 'vlr-client';

const vlr = new VlrClient();

async function main() {
  // Try fetching a known player - TenZ has ID 9 on VLR.gg
  try {
    const { data: player } = await vlr.getPlayerById('9');
    console.log('Player found:', JSON.stringify(player, null, 2));
  } catch (e) {
    console.error('Error fetching player 9:', e.message);
  }
}

main();

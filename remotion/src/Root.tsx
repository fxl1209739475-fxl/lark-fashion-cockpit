import {Composition} from "remotion";
import {OutfitCard} from "./OutfitCard";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* 9:16 抖音/小红书竖屏，5 秒，30fps */}
      <Composition
        id="OutfitCard"
        component={OutfitCard}
        durationInFrames={150}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          title: "今日穿搭灵感",
          subtitle: "DRS-0429-FL · 法式碎花连衣裙",
          tags: ["#日常通勤", "#显瘦", "#155-165", "#新品"],
          price: "¥299",
        }}
      />
    </>
  );
};

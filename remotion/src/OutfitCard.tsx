import {AbsoluteFill, useCurrentFrame, interpolate, spring, useVideoConfig} from "remotion";

interface Props {
  title: string;
  subtitle: string;
  tags: string[];
  price: string;
}

export const OutfitCard: React.FC<Props> = ({title, subtitle, tags, price}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  // 标题淡入 + 上滑
  const titleOpacity = interpolate(frame, [0, 20], [0, 1], {extrapolateRight: "clamp"});
  const titleY = interpolate(frame, [0, 30], [40, 0], {extrapolateRight: "clamp"});

  // 副标题延迟出现
  const subOpacity = interpolate(frame, [15, 35], [0, 1], {extrapolateRight: "clamp"});

  // 标签 stagger 弹性进入
  const tagSprings = tags.map((_, i) =>
    spring({frame: frame - 30 - i * 8, fps, config: {damping: 10}})
  );

  // 价格弹跳
  const priceScale = spring({frame: frame - 60, fps, from: 0, to: 1, config: {damping: 8}});

  return (
    <AbsoluteFill
      style={{
        background: "linear-gradient(135deg, #FFE4E1 0%, #FFB6C1 100%)",
        justifyContent: "center",
        alignItems: "center",
        padding: 80,
        fontFamily: "PingFang SC, -apple-system, sans-serif",
      }}
    >
      <div style={{textAlign: "center", color: "#3a2a2a"}}>
        <div
          style={{
            fontSize: 92,
            fontWeight: 800,
            letterSpacing: -2,
            opacity: titleOpacity,
            transform: `translateY(${titleY}px)`,
            marginBottom: 24,
          }}
        >
          {title}
        </div>

        <div
          style={{
            fontSize: 48,
            fontWeight: 500,
            opacity: subOpacity,
            color: "#7a4a4a",
            marginBottom: 80,
          }}
        >
          {subtitle}
        </div>

        <div style={{display: "flex", gap: 16, flexWrap: "wrap", justifyContent: "center", marginBottom: 100}}>
          {tags.map((tag, i) => (
            <div
              key={tag}
              style={{
                fontSize: 36,
                background: "rgba(255,255,255,0.8)",
                padding: "16px 32px",
                borderRadius: 100,
                color: "#a04060",
                fontWeight: 600,
                opacity: tagSprings[i],
                transform: `scale(${tagSprings[i]})`,
              }}
            >
              {tag}
            </div>
          ))}
        </div>

        <div
          style={{
            fontSize: 140,
            fontWeight: 900,
            color: "#d63a5a",
            transform: `scale(${priceScale})`,
            display: "inline-block",
          }}
        >
          {price}
        </div>
      </div>
    </AbsoluteFill>
  );
};

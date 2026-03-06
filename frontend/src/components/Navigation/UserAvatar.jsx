import useAuthStore from "../../store/useAuthStore";

export default function UserAvatar({ size = "md" }) {
  const user = useAuthStore((state) => state.user);

  const dimensions = {
    sm: "w-8 h-8 text-xs",
    md: "w-10 h-10 text-sm",
    lg: "w-12 h-12 text-base",
  }[size];

  const photoURL =
    user?.photoURL ||
    `https://ui-avatars.com/api/?name=${encodeURIComponent(user?.displayName || "User")}&background=0D8ABC&color=fff&bold=true`;

  return (
    <img
      src={photoURL}
      alt={user?.displayName || "User"}
      className={`${dimensions} rounded-full object-cover border-2 border-white dark:border-gray-800 shadow-sm`}
    />
  );
}

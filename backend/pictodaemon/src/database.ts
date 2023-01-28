// GNU AGPL v3 License
// Written by John Nunley

// Database backend for PictoDaemon
export default abstract class Database {
  // Initialize the database.
  public abstract init(): Promise<void>;

  // Functions for getting and updating user data.
  public abstract getUser(id: number): Promise<User>;
  public abstract addUser(user: NewUser): Promise<User>;
  public abstract updateUser(user: UpdateUser): Promise<void>;
}

// Unique ID for an object
export type ID = number;

// User data
export interface User {
  id: ID;
  username: string;
  realname: string;
}

export type NewUser = Omit<User, "id">;
export type UpdateUser = Partial<NewUser> & Pick<User, "id">;

import { Table, Column, Model, DataType } from 'sequelize-typescript';

@Table({ tableName: 'logs', timestamps: false })
export class Log extends Model {
    @Column({ type: DataType.STRING, allowNull: false })
    fileName: string;

    @Column({ type: DataType.STRING, allowNull: false })
    sessao: string;

    @Column({ type: DataType.STRING, allowNull: false })
    node: string;

    @Column({ type: DataType.DATE, allowNull: false, defaultValue: DataType.NOW })
    date: Date;
}

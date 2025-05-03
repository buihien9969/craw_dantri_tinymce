<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;
use Illuminate\Support\Facades\DB;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        // Kiểm tra xem bảng moderation_logs đã tồn tại chưa
        if (Schema::hasTable('moderation_logs')) {
            // Kiểm tra xem cột log_id đã tồn tại chưa
            if (!Schema::hasColumn('moderation_logs', 'log_id') && Schema::hasColumn('moderation_logs', 'id')) {
                // Đổi tên cột id thành log_id
                Schema::table('moderation_logs', function (Blueprint $table) {
                    $table->renameColumn('id', 'log_id');
                });
            }
            
            // Thêm các cột cần thiết nếu chưa tồn tại
            Schema::table('moderation_logs', function (Blueprint $table) {
                if (!Schema::hasColumn('moderation_logs', 'action_type')) {
                    $table->enum('action_type', ['approve', 'reject', 'flag', 'edit', 'delete', 'restore', 'auto_moderate'])->nullable();
                }
                
                if (!Schema::hasColumn('moderation_logs', 'content_type')) {
                    $table->enum('content_type', ['article', 'comment', 'user', 'category', 'role_upgrade'])->nullable();
                }
                
                if (!Schema::hasColumn('moderation_logs', 'content_id')) {
                    $table->unsignedBigInteger('content_id')->nullable();
                }
                
                if (!Schema::hasColumn('moderation_logs', 'moderator_id')) {
                    $table->unsignedBigInteger('moderator_id')->nullable();
                }
                
                if (!Schema::hasColumn('moderation_logs', 'details')) {
                    $table->text('details')->nullable();
                }
                
                if (!Schema::hasColumn('moderation_logs', 'before_state')) {
                    $table->text('before_state')->nullable();
                }
                
                if (!Schema::hasColumn('moderation_logs', 'after_state')) {
                    $table->text('after_state')->nullable();
                }
                
                if (!Schema::hasColumn('moderation_logs', 'severity')) {
                    $table->enum('severity', ['none', 'low', 'medium', 'high'])->default('none');
                }
            });
            
            // Thêm foreign key nếu chưa tồn tại
            if (!Schema::hasColumn('moderation_logs', 'moderator_id')) {
                Schema::table('moderation_logs', function (Blueprint $table) {
                    $table->foreign('moderator_id')
                        ->references('user_id')
                        ->on('users')
                        ->onDelete('set null');
                });
            }
        }
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        // Không cần thực hiện gì trong phương thức down
    }
};
